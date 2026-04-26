from langchain_core.messages import HumanMessage, SystemMessage

from configs.config import Config

from ..common.constants import STRUCTURED_METHOD
from ..common.llm_factory import make_supervisor_llm
from ..prompts.supervisor import SUPERVISOR_TEMPLATE
from .models.supervisor_output import SupervisorDecision


class SupervisorNode:
    def __init__(self):
        self.config = Config()
        self.llm = make_supervisor_llm().with_structured_output(
            SupervisorDecision, method=STRUCTURED_METHOD
        )

    def __call__(self, state):
        errors = (
            "; ".join(f"{e.agent}: {e.message[:150]}" for e in state.errors[-3:])
            if state.errors
            else "(нет)"
        )
        prompt = SUPERVISOR_TEMPLATE.format(
            business_task=state.business_task,
            target_column=state.target_column,
            dataset_path=state.dataset_path,
            iteration=state.iteration,
            max_iterations=self.config.MAX_SUPERVISOR_ITERATIONS,
            has_de="yes" if state.data_engineer_report else "no",
            has_da="yes" if state.data_analyst_report else "no",
            has_ds="yes" if state.data_scientist_report else "no",
            de_iter=state.de_iteration,
            da_iter=state.da_iteration,
            ds_iter=state.ds_iteration,
            errors=errors,
        )
        decision = self.llm.invoke(
            [SystemMessage(prompt), HumanMessage("Reason about state and pick next_agent.")]
        )

        if state.iteration >= self.config.MAX_SUPERVISOR_ITERATIONS - 1:
            decision = decision.model_copy(update={"next_agent": "finish", "instruction": ""})

        update = {
            "next_agent": decision.next_agent,
            "iteration": state.iteration + 1,
            "supervisor_feedback": decision.instruction,
        }
        if decision.next_agent == "data_engineer":
            update["de_iteration"] = state.de_iteration + 1
        elif decision.next_agent == "data_analyst":
            update["da_iteration"] = state.da_iteration + 1
        elif decision.next_agent == "data_scientist":
            update["ds_iteration"] = state.ds_iteration + 1
        return update
