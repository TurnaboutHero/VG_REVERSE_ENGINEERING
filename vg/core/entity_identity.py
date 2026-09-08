"""Recording-scoped spawn observations; never infer kill credit or ownership."""
from dataclasses import dataclass
import struct
from .definition_catalog import CatalogError, DefinitionCatalog
from .vgr_records import VGRRecord


@dataclass(frozen=True)
class SpawnIdentity:
    recording_id: str
    observation: int
    section: int
    record_offset: int
    timestamp: float
    opcode: int
    entity_id: int
    definition_index: int
    skin_hash: int
    definition_name: str | None
    kind: str
    status: str
    previous_observation: int | None
    transition: str
    raw_payload_hex: str
    build_sha256: str
    manifest_sha256: str
    owner_entity_id: int | None = None
    credited_player_id: int | None = None


class EntityResolver:
    """One instance per recording, fed strictly in section/record order.

    Each spawn is an observation boundary, not proof of a new lifetime.
    Repeated same-definition spawns may be snapshots or respawns. A changed
    definition is preserved as a change, without inferring morph or ID reuse. No resolution before the first spawn;
    no destruction/despawn or persistence across recordings is inferred.
    """
    def __init__(self, recording_id: str, catalog: DefinitionCatalog, build_sha256: str):
        if not recording_id:
            raise ValueError('recording_id is required')
        if build_sha256 != catalog.profile.build_sha256:
            raise CatalogError('recording build does not match catalog')
        self.recording_id = recording_id
        self.catalog = catalog
        self._latest = {}
        self._last_position = None
        self._observation = 0

    def observe(self, record: VGRRecord, section: int = 0):
        position = (section, record.offset)
        if section < 0 or (self._last_position is not None and position <= self._last_position):
            raise ValueError('records must be fed once in section/offset order')
        self._last_position = position
        if record.opcode not in (0x03f2, 0x03f3):
            return None
        observed_lengths = {0x03f2: (122, 126), 0x03f3: (746, 750)}
        if (len(record.payload) not in observed_lengths[record.opcode]
                or record.content_length != len(record.payload) + 2):
            raise ValueError('unsupported or truncated native spawn layout')
        index, skin, entity = struct.unpack_from('>III', record.payload)
        try:
            definition = self.catalog.lookup(index)
            name, kind, status = definition.name, definition.kind, 'resolved'
        except CatalogError:
            name, kind, status = None, 'unknown', 'definition_index_out_of_range'
        previous = self._latest.get(entity)
        transition = 'first_observation'
        if previous is not None:
            transition = ('repeated_spawn_lifetime_unknown' if previous.definition_index == index
                          else 'definition_changed')
        self._observation += 1
        identity = SpawnIdentity(
            self.recording_id, self._observation, section, record.offset,
            record.timestamp, record.opcode, entity, index, skin, name, kind,
            status, previous.observation if previous else None, transition,
            bytes(record.payload).hex(), self.catalog.profile.build_sha256,
            self.catalog.profile.manifest_sha256,
        )
        self._latest[entity] = identity
        return identity

    def latest_observed(self, entity_id: int):
        """Return prior spawn evidence, not a claim that the actor is still alive."""
        return self._latest.get(entity_id)
