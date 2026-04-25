# Agent 设计文档

## Agent 基类

```python
class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    @abstractmethod
    def process(self, state: Dict) -> Dict:
        pass
```

## DemandAnalyst (需求分析师)

### 职责
- 解析自然语言需求
- 生成结构化子需求列表
- 生成验收标准 (Given-When-Then)
- 评估复杂度

### 输入
- `raw_requirement`: 自然语言需求文本

### 输出
- `structured_requirements`: 子需求列表
- `acceptance_criteria`: 验收标准
- `estimated_complexity`: 复杂度评估

### 提示词模板
```
你是资深需求分析师。根据以下需求文本，进行结构化分析。
需求文本：{requirement_text}
请输出 JSON 格式的子需求列表和验收标准...
```

## Architect (架构师)

### 职责
- 分析需求并设计系统架构
- 确定技术栈
- 定义模块接口
- 生成任务拆分计划

### 输入
- `structured_requirements`: 子需求列表

### 输出
- `architecture_doc`: 架构文档
- `tech_stack`: 技术栈选型
- `integration_points`: 接口定义

## DetailDesigner (详细设计师)

### 职责
- 将架构拆解为具体任务
- 绑定测试用例
- 生成依赖图

### 输入
- `architecture_doc`: 架构文档

### 输出
- `detailed_tasks`: 详细任务列表
- `task_graph`: 任务依赖图

## Developer (开发者)

### 职责
- 接收任务并实现代码
- 运行单元测试
- 提交代码并汇报结果

### 输入
- `task`: 任务详情

### 输出
- `ExecutionResult`: 执行结果

## Tester (测试工程师)

### 职责
- 执行测试套件
- 截图对比测试
- 生成测试报告

## GamePlayEvaluator (游戏性评估)

### 职责
- 启动游戏并执行操作
- 分析帧率和反馈
- 生成游戏性评价

### 工具集
- Godot 远程控制
- 计算机视觉 (YOLO/OCR)
- 音频分析
