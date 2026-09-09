"""Recording-scoped spawn and destroy-action evidence, not actor lifetimes."""
from dataclasses import dataclass
import struct
from .definition_catalog import CatalogError, DefinitionCatalog, EntityKindEvidence
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
    previous_destroy_observation: int | None = None
    kind_evidence: EntityKindEvidence | None = None


@dataclass(frozen=True)
class DestroyObservation:
    recording_id: str
    observation: int
    section: int
    record_offset: int
    timestamp: float
    opcode: int
    entity_id: int
    previous_spawn_observation: int | None
    raw_payload_hex: str
    build_sha256: str
    manifest_sha256: str


@dataclass(frozen=True)
class LifecycleEvidence:
    recording_id: str
    entity_id: int
    status: str
    latest_spawn_observation: int | None
    latest_destroy_observation: DestroyObservation | None


class EntityResolver:
    """One instance per recording, fed strictly in section/record order.

    Each spawn is an observation boundary, not proof of a new lifetime.
    Repeated same-definition spawns may be snapshots or respawns. A changed
    definition is preserved as a change, without inferring morph or ID reuse.
    Destroy actions are recorded separately from historical spawn identities:
    their presence does not prove actor lookup, native execution or cleanup.
    No resolution before the first spawn or across recordings is inferred.
    """
    def __init__(self, recording_id: str, catalog: DefinitionCatalog, build_sha256: str):
        if not recording_id:
            raise ValueError('recording_id is required')
        if build_sha256 != catalog.profile.build_sha256:
            raise CatalogError('recording build does not match catalog')
        self.recording_id = recording_id
        self.catalog = catalog
        self._latest: dict[int, SpawnIdentity] = {}
        self._latest_destroy: dict[int, DestroyObservation] = {}
        self._last_position: tuple[int, int] | None = None
        self._observation = 0

    def observe(self, record: VGRRecord, section: int = 0) -> SpawnIdentity | DestroyObservation | None:
        position = (section, record.offset)
        if section < 0 or (self._last_position is not None and position <= self._last_position):
            raise ValueError('records must be fed once in section/offset order')
        self._last_position = position
        if record.opcode == 0x040b:
            # All 1,242 observed actions have a BE u32 ID and two opaque bytes.
            if len(record.payload) != 6 or record.content_length != 8:
                raise ValueError('unsupported or truncated native destroy-action layout')
            entity = struct.unpack_from('>I', record.payload)[0]
            if entity == 0xFFFFFFFF:
                return None
            previous = self._latest.get(entity)
            self._observation += 1
            destroy = DestroyObservation(
                self.recording_id, self._observation, section, record.offset,
                record.timestamp, record.opcode, entity,
                previous.observation if previous else None,
                bytes(record.payload).hex(), self.catalog.profile.build_sha256,
                self.catalog.profile.manifest_sha256,
            )
            self._latest_destroy[entity] = destroy
            return destroy
        if record.opcode not in (0x03f2, 0x03f3):
            return None
        observed_lengths = {0x03f2: (122, 126), 0x03f3: (746, 750)}
        if (len(record.payload) not in observed_lengths[record.opcode]
                or record.content_length != len(record.payload) + 2):
            raise ValueError('unsupported or truncated native spawn layout')
        index, skin, entity = struct.unpack_from('>III', record.payload)
        if entity == 0xFFFFFFFF:
            return None
        try:
            definition = self.catalog.lookup(index)
            name, kind, status = definition.name, definition.kind, 'resolved'
            kind_evidence = definition.kind_evidence
        except CatalogError:
            name, kind, status = None, 'unknown', 'definition_index_out_of_range'
            kind_evidence = None
        previous = self._latest.get(entity)
        destroy = self._latest_destroy.get(entity)
        after_destroy = destroy is not None and (
            previous is None or destroy.observation > previous.observation)
        transition = 'first_observation'
        if after_destroy:
            transition = 'spawn_after_destroy_observation'
        elif previous is not None:
            transition = ('repeated_spawn_lifetime_unknown' if previous.definition_index == index
                          else 'definition_changed')
        self._observation += 1
        identity = SpawnIdentity(
            self.recording_id, self._observation, section, record.offset,
            record.timestamp, record.opcode, entity, index, skin, name, kind,
            status, previous.observation if previous else None, transition,
            bytes(record.payload).hex(), self.catalog.profile.build_sha256,
            self.catalog.profile.manifest_sha256,
            previous_destroy_observation=(destroy.observation
                                          if destroy is not None and after_destroy else None),
            kind_evidence=kind_evidence,
        )
        self._latest[entity] = identity
        return identity

    def latest_observed(self, entity_id: int) -> SpawnIdentity | None:
        """Return prior spawn evidence, not a claim that the actor is still alive."""
        return self._latest.get(entity_id)

    def lifecycle_evidence(self, entity_id: int) -> LifecycleEvidence:
        """Return ordered action evidence without claiming the actor's live state."""
        spawn = self._latest.get(entity_id)
        destroy = self._latest_destroy.get(entity_id)
        status = 'spawn_observed' if spawn is not None else 'unobserved'
        if destroy is not None and (spawn is None or destroy.observation > spawn.observation):
            status = 'destroy_action_observed'
        return LifecycleEvidence(
            self.recording_id, entity_id, status,
            spawn.observation if spawn else None, destroy,
        )
