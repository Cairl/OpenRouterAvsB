export interface ModelPricing {
  prompt_per_m: number;
  completion_per_m: number;
  prompt_per_m_usd: number;
  completion_per_m_usd: number;
}

export interface AAIndices {
  intelligence: number | null;
  coding: number | null;
  agentic: number | null;
}

export interface AAPercentiles {
  intelligence_percentile: number | null;
  coding_percentile: number | null;
  agentic_percentile: number | null;
}

export interface DesignArenaCategory {
  elo: number;
  win_rate: number;
}

export interface DesignArenaData {
  models_arena: Record<string, DesignArenaCategory>;
  agents_arena: Record<string, DesignArenaCategory>;
}

export interface ModelData {
  id: string;
  name: string;
  provider: string;
  context_length: number;
  max_output: number;
  created: number;
  canonical_slug: string;
  pricing: ModelPricing;
  modality: string;
  aa_indices: AAIndices;
  aa_percentiles: AAPercentiles;
  benchmarks: Record<string, number>;
  design_arena: DesignArenaData;
  error: string | null;
}

export interface BenchmarksResponse {
  data: ModelData[];
  failed: string[];
  exchange_rate: number;
}

export const BENCHMARK_LABELS: Record<string, string> = {
  "GPQA Diamond": "研究生级科学推理",
  "HLE": "人类最后的考试",
  "SciCode": "用于科学计算的 Python 编程",
  "Terminal-Bench Hard": "智能体编程与终端调用",
  "AA-LCR": "长文本推理评估",
  "IFBench": "指令遵循基准",
  "GDPval-AA": "具经济价值的任务",
  "CritPt": "研究级物理推理",
  "τ²-Bench Telecom": "双控场景下的对话式 AI 智能体",
  "AA-Omniscience Accuracy": "正确回答问题的比例",
  "AA-Omniscience Non-Hallucination Rate": "未正确回答中避免幻觉的比例",
  "AA-Omniscience Hallucination Rate": "幻觉率",
};

export const BENCHMARK_DESCRIPTIONS: Record<string, string> = {
  "GPQA Diamond": "评估大语言模型在研究生层次科学推理能力的高难度基准测试，题目覆盖物理、化学和生物学等领域，由领域专家设计并达成共识，确保无法通过简单网络搜索获得答案，钻石子集代表其中质量与难度最高的题目集合。",
  "HLE": "衡量人工智能系统在跨学科极限知识与推理能力上表现的超大规模测试集，汇聚了各学科专家提出的数千道高难度问题，旨在作为检验模型能否达到人类认知终点的终极挑战。",
  "IFBench": "系统性评价大语言模型对复杂指令遵循能力的基准，涵盖格式、内容、风格、长度等多重约束类型，以检验模型能否精准执行详细的任务要求，而非产生偏离或遗漏。",
  "τ²-Bench Telecom": "评估对话式人工智能智能体在电信领域双重控制场景下表现的基准平台，模拟客服与用户均可主动发起控制权的复杂对话，考察智能体在多轮交互中的决策、工具调用与任务完成能力。",
  "AA-LCR": "测试模型在极长上下文条件下进行复杂推理能力的评估框架，通过需要横跨大量文本片段进行逻辑整合的问题，检验模型对长程依赖与信息检索的综合处理水平。",
  "GDPval-AA": "衡量模型在具有直接经济价值的真实任务上表现的基准，覆盖财务分析、商业决策和数据解释等高影响力场景，以评估人工智能系统提升生产力的实际潜力。",
  "CritPt": "考察模型进行研究级物理推理能力的评测集，题目源自前沿物理学问题，要求模型展示理论推导、物理概念运用和数学建模等高阶科学研究技能。",
  "SciCode": "评估模型根据自然科学问题描述编写Python程序以求解科学计算任务能力的基准，涵盖物理、化学、生物等学科的数值模拟、数据处理与方程求解等实际编程问题。",
  "Terminal-Bench Hard": "测评人工智能智能体在命令行终端环境中自主完成复杂编码与系统操作任务的困难基准，要求模型像人类一样使用终端工具、操控文件、调试程序并解决多步骤工作流程。",
  "AA-Omniscience Accuracy": "衡量模型在AA-Omniscience全知评测中正确回答问题的比例，直接反映模型在广泛知识领域内给出准确答案的综合能力。",
  "AA-Omniscience Non-Hallucination Rate": "评估模型在回答错误时仍能避免产生幻觉的比率，即在不正确响应中保持信息真实性、不编造虚假内容的样本占比，用以衡量模型的安全可靠程度。",
  "AA-Omniscience Hallucination Rate": "模型产生幻觉或虚构回答的比例",
};
