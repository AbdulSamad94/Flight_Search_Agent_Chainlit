import chainlit as cl
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
    AsyncOpenAI,
    RunConfig,
)

from config import GEMINI_API_KEY
from tools import get_flights, get_city_airport_code
from agent_config import AGENT_INSTRUCTIONS

set_tracing_disabled(disabled=True)


@cl.on_chat_start
async def start():
    """Initialize the chat session with agent configuration"""
    external_client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash", openai_client=external_client
    )

    config = RunConfig(
        model=model, model_provider=external_client, tracing_disabled=True
    )

    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    # Create the flight assistant agent
    agent: Agent = Agent(
        name="Flight Assistant",
        instructions=AGENT_INSTRUCTIONS,
        model=model,
        tools=[get_flights, get_city_airport_code],
    )
    cl.user_session.set("agent", agent)

    await cl.Message(
        content="Welcome to the AI Flight Assistant!\n\nI can help you find flights for today. Just tell me where you want to fly from and to, you can use city names or airport codes. How can I help you today?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and process flight requests"""

    msg = cl.Message(content="")
    await msg.send()

    msg.content = "Thinking..."
    await msg.update()

    agent: Agent = cl.user_session.get("agent")
    config: RunConfig = cl.user_session.get("config")
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_sync(agent, history, run_config=config)

        # Clear the thinking message and prepare for streaming
        msg.content = ""
        await msg.update()

        # Stream the response
        full_response = "Thinking"

        # Get the final response
        response_content = result.final_output

        # If we have a complete response, use it; otherwise use streamed content
        if response_content:
            msg.content = response_content
        else:
            msg.content = full_response

        await msg.update()

        # Update chat history
        history.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("chat_history", history)

        # for tha Debug logging
        print(f"User: {message.content}")
        print(f"Assistant: {msg.content}")

    except Exception as e:
        error_message = f"Error: {str(e)}\n\nPlease try again or contact support if the problem persists."
        msg.content = error_message
        await msg.update()
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    cl.run()
