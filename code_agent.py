from autogen import config_list_from_json
import autogen
import random

# Get api key
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
llm_config = {"model": "gpt-3.5-turbo", "config_list": config_list, "seed": random.randint(1, 19099), "request_timeout": 120}

# Create user proxy agent, coder, product manager
user_proxy = autogen.UserProxyAgent(
    name="admin",
    system_message="You are a human admin who will give the idea. You don't write code. You ask coder to write code. If problem resolved, you say TERMINATE.",
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="TERMINATE",
)

coder = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config,
)

executor = autogen.UserProxyAgent(
    name="Executor",
    llm_config=False,
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 2, "work_dir": "groupchat"},
    default_auto_reply="No code provided, coder, can you provide code?"
)

pm = autogen.AssistantAgent(
    name="Planner",
    system_message="You will help break down the initial idea into a well scoped requirement for the coder; Do not involve in future conversations or error fixing",
    llm_config=llm_config,
)

# Create groupchat
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, pm, executor], messages=[], max_round=50)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# set up self-introduction that specific to the current group chat
# this is optional but recommended, which helps groupchat manager to select the right agent to carry on the conversation
# it also help seperate the introduction message from system message
# therefore you can craft more delicated system message that are only visible to the agent itself
user_proxy.send("Hi, I am admin, welcome to the group. Work together to resolve my idea. I will give you the idea", manager, False)
coder.send("Hi, I am coder, I will help admin build the game", manager, False)
pm.send("Hi, I am planner, I will help admin break down the idea", manager, False)
executor.send("Hi, I am executor, I will help coder execute the code", manager, False)
user_proxy.send("planner, you break down my idea into well_scoped requirements for coder. Then coder, implement each requirement one by one", manager, False)
# Start the conversation
user_proxy.initiate_chat(
    manager, message="Build a classic & basic pong game with 2 players in python")
