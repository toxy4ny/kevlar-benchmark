from .poetry_local import PoetryLocalAttack
from .reprompt_copilot_leak import RepromptCopilotLeak

EXTENSIONS = {
    PoetryLocalAttack.name(): PoetryLocalAttack,
    RepromptCopilotLeak.name(): RepromptCopilotLeak,
}