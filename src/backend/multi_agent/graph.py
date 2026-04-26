from langgraph.graph import END, START, StateGraph

from .agents.data_analyst.agent import DataAnalystAgent
from .agents.data_engineer.agent import DataEngineerAgent
from .agents.data_scientist.agent import DataScientistAgent
from .models.enums.node_names import NodeNames
from .models.state import State
from .nodes.finalize import FinalizeNode
from .nodes.supervisor import SupervisorNode


class MultiAgentGraph:
    def __init__(self):
        g = StateGraph(State)

        g.add_node(NodeNames.SUPERVISOR, SupervisorNode())
        g.add_node(NodeNames.DATA_ENGINEER, DataEngineerAgent())
        g.add_node(NodeNames.DATA_ANALYST, DataAnalystAgent())
        g.add_node(NodeNames.DATA_SCIENTIST, DataScientistAgent())
        g.add_node(NodeNames.FINALIZE, FinalizeNode())

        g.add_edge(START, NodeNames.SUPERVISOR)
        g.add_conditional_edges(
            NodeNames.SUPERVISOR,
            lambda s: s.next_agent or "finish",
            {
                NodeNames.DATA_ENGINEER: NodeNames.DATA_ENGINEER,
                NodeNames.DATA_ANALYST: NodeNames.DATA_ANALYST,
                NodeNames.DATA_SCIENTIST: NodeNames.DATA_SCIENTIST,
                "finish": NodeNames.FINALIZE,
            },
        )
        g.add_edge(NodeNames.DATA_ENGINEER, NodeNames.SUPERVISOR)
        g.add_edge(NodeNames.DATA_ANALYST, NodeNames.SUPERVISOR)
        g.add_edge(NodeNames.DATA_SCIENTIST, NodeNames.SUPERVISOR)
        g.add_edge(NodeNames.FINALIZE, END)

        self.graph = g.compile()
