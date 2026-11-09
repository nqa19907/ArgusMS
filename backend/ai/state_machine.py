from dataclasses import dataclass
from datetime import datetime, timezone
from backend.contracts import FallCandidate, StateTransition


def _mono_to_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class _TrackEpisodeState:
    state: str = "WARMUP"
    valid_samples: int = 0
    last_mono: float | None = None
    suspected_since_mono: float | None = None
    onset_utc: str = ""
    recovery_since_mono: float | None = None
    last_confirmed_mono: float | None = None
    episode_counter: int = 0
    active_episode_id: str = ""


class FallStateMachine:
    def __init__(
        self,
        confirmation_seconds: float = 2.0,
        recovery_seconds: float = 3.0,
        cooldown_seconds: float = 60.0,
        max_pose_gap_seconds: float = 0.3,
        warmup_samples: int = 5,
        enter_threshold: float = 0.65,
    ) -> None:
        self.confirmation_seconds = confirmation_seconds
        self.recovery_seconds = recovery_seconds
        self.cooldown_seconds = cooldown_seconds
        self.max_pose_gap_seconds = max_pose_gap_seconds
        self.warmup_samples = warmup_samples
        self.enter_threshold = enter_threshold
        self._tracks: dict[tuple[str, int], _TrackEpisodeState] = {}

    def reset(self, stream_session_id: str | None = None) -> None:
        if stream_session_id is None:
            self._tracks.clear()
        else:
            keys = [k for k in self._tracks if k[0] == stream_session_id]
            for k in keys:
                del self._tracks[k]

    def update(
        self,
        camera_id: str,
        stream_session_id: str,
        candidate: FallCandidate,
        captured_mono: float,
        model_id: str,
    ) -> StateTransition:
        key = (stream_session_id, candidate.track_id)
        st = self._tracks.setdefault(key, _TrackEpisodeState())

        if st.last_mono is not None and (captured_mono - st.last_mono) > self.max_pose_gap_seconds:
            if st.state != "LATCHED":
                st.state = "UNKNOWN"
                st.valid_samples = 0
                st.suspected_since_mono = None
                st.recovery_since_mono = None

        st.last_mono = captured_mono

        if not candidate.valid_pose:
            if st.state != "LATCHED":
                st.state = "UNKNOWN"
                st.valid_samples = 0
                st.suspected_since_mono = None
            return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

        if st.state in ("WARMUP", "UNKNOWN"):
            st.valid_samples += 1
            if st.valid_samples >= self.warmup_samples:
                st.state = "NORMAL"
            return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

        if st.state == "NORMAL":
            cooldown_ok = (
                st.last_confirmed_mono is None
                or (captured_mono - st.last_confirmed_mono) >= self.cooldown_seconds
            )
            if cooldown_ok and candidate.onset_observed and candidate.score >= self.enter_threshold:
                st.state = "SUSPECTED"
                st.suspected_since_mono = captured_mono
                st.onset_utc = _mono_to_utc_str()
            return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

        if st.state == "SUSPECTED":
            if not candidate.low_posture or candidate.score < (self.enter_threshold * 0.8):
                st.state = "NORMAL"
                st.suspected_since_mono = None
                return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

            if st.suspected_since_mono is not None and (
                captured_mono - st.suspected_since_mono
            ) >= self.confirmation_seconds:
                st.episode_counter += 1
                st.active_episode_id = f"ep-{stream_session_id}-track{candidate.track_id}-{st.episode_counter:03d}"
                st.last_confirmed_mono = captured_mono
                st.state = "LATCHED"
                return self._build_transition(
                    st, camera_id, stream_session_id, candidate, model_id, True, override_state="CONFIRMED"
                )
            return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

        if st.state in ("LATCHED", "RECOVERY"):
            if not candidate.low_posture:
                if st.recovery_since_mono is None:
                    st.recovery_since_mono = captured_mono
                    st.state = "RECOVERY"
                elif (captured_mono - st.recovery_since_mono) >= self.recovery_seconds:
                    st.state = "NORMAL"
                    st.recovery_since_mono = None
                    st.suspected_since_mono = None
            else:
                st.state = "LATCHED"
                st.recovery_since_mono = None
            return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

        return self._build_transition(st, camera_id, stream_session_id, candidate, model_id, False)

    @staticmethod
    def _build_transition(
        st: _TrackEpisodeState,
        camera_id: str,
        stream_session_id: str,
        candidate: FallCandidate,
        model_id: str,
        just_confirmed: bool,
        override_state: str | None = None,
    ) -> StateTransition:
        now_utc = _mono_to_utc_str()
        return StateTransition(
            state=(override_state or st.state),  # type: ignore[arg-type]
            just_confirmed=just_confirmed,
            episode_id=st.active_episode_id or f"ep-{stream_session_id}-track{candidate.track_id}-000",
            camera_id=camera_id,
            stream_session_id=stream_session_id,
            track_id=candidate.track_id,
            occurred_at_utc=st.onset_utc or now_utc,
            confirmed_at_utc=now_utc,
            score=candidate.score,
            score_kind=candidate.score_kind,
            model_id=model_id,
            reasons=candidate.reasons,
        )