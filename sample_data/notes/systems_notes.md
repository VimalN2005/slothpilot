# Distributed Systems & Placement Notes

Key preparation notes for upcoming backend interviews.

## Raft Consensus Engine
- Raft decomposes consensus into leader election, log replication, and safety.
- Leaders maintain `nextIndex[]` and `matchIndex[]` arrays for each peer.
- Heartbeats sent every 50ms to prevent split-brain elections.

## Action Items
- [ ] Implement mini-Raft state machine in Python
- [ ] Review OpenTelemetry baggage propagation RFC
- [ ] Prepare mock interview demo for IIIT junior
