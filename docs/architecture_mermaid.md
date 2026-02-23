# QNME Architecture (Mermaid)

```mermaid
flowchart TB
  subgraph DataLayer
    Ticks[Market Ticks (DhanFetcher / WsProvider)]
    L0[Layer 0: Market Genome (GENOME+)]
  end

  subgraph Regime
    L1[Layer 1: Market Regime (16 micro-regimes)]
  end

  subgraph StrategyPool
    L2[Layer 2: Adaptive Strategy Pool (30 strategies)]
    L3[Layer 3: Multi-Stage Signal Validation (18 gates)]
    L4[Layer 4: Meta-Strategy Controller (Neuromorphic)]
  end

  subgraph LearnMutate
    L5[Layer 5: Evolutionary Learning Loop]
    L6[Layer 6: Strategy Mutation Engine]
    L7[Layer 7: Strategy Fusion Engine]
  end

  subgraph MacroRisk
    L8[Layer 8: Long-Horizon Intelligence]
    L9[Layer 9: Risk Intelligence Engine]
    L10[Layer 10: Anomaly Detection]
    L11[Layer 11: Meta-Cognitive Override]
  end

  Ticks --> L0 --> L1
  L1 --> L2
  L2 --> L3 --> L4
  L4 -->|Validated decisions| Execution[Order Manager & Execution Engine]
  L4 --> L5 --> L6 --> L7 --> L4
  L8 --> L4
  Execution --> L9
  L9 --> L11
  L10 --> L11
  L11 --> Execution
  subgraph Persistence
    SeqDB[(SeqStore / Audit / Replay DB)]
    ModelStore[(Model/Strategy Store)]
    Metrics[(Prometheus / TSDB)]
  end
  Ticks --> SeqDB
  L5 --> ReplayDB[(Replay Buffer)]
  L6 --> ModelStore
  L7 --> ModelStore
  L4 --> Metrics
  L9 --> Metrics
