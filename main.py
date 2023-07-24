from chainlit.server import app, get_html_template
import mimetypes

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")

import os
import webbrowser
from pathlib import Path


from contextlib import asynccontextmanager
from watchfiles import awatch

from fastapi import FastAPI, Request, Response
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
    FileResponse,
    PlainTextResponse,
)
from fastapi_socketio import SocketManager
from starlette.middleware.cors import CORSMiddleware
import asyncio

from chainlit.config import config, load_module, reload_config, DEFAULT_HOST
from chainlit.client.utils import (
    get_auth_client_from_request,
    get_db_client_from_request,
)
from chainlit.markdown import get_markdown_str
from chainlit.telemetry import trace_event
from chainlit.logger import logger
from chainlit.types import (
    CompletionRequest,
    UpdateFeedbackRequest,
    GetConversationsRequest,
    DeleteConversationRequest,
)
import requests
import jwt
import chainlit as cl
from chainlit.user_session import user_sessions
import uuid

REDIRECT_URL = "https://5308-2001-ee0-d741-2e60-bc8b-cf66-64f1-4a36.ngrok-free.app/helloworld"
OIDC_CLIENT_ID = "PTwTcOE0RfUeMPqs2IOX8JMtiwpQa6q5qD0IIFnf4rY"
OIDC_CLIENT_SECRET = "2GLvdawMDJzJxsp13rsDf4Y4-CfMKSTlB-thAsUjIjk"
login="https://pressingly-account.onrender.com/oauth/authorize?client_id=PTwTcOE0RfUeMPqs2IOX8JMtiwpQa6q5qD0IIFnf4rY&redirect_uri=https%3A%2F%2F5308-2001-ee0-d741-2e60-bc8b-cf66-64f1-4a36.ngrok-free.app%2Fhelloworld&response_type=code&scope=openid+email"

chainlit_route = app.router.routes

from chainlit.server import html_template
print(html_template)
@app.get("/")
async def serve(request: Request):
    html_template = get_html_template()
    """Serve the UI files."""

    response = HTMLResponse(content=html_template, status_code=200)
    auth_email = request.cookies.get('auth_email')
    print("auth_email", auth_email)

    chainlit_session_id = str(uuid.uuid4())
    response.set_cookie(
        key="chainlit-session", value=chainlit_session_id, httponly=True
    )
    user_sessions[chainlit_session_id] = {"auth_email": auth_email}




    return response

@app.get("/helloworld")
async def helloworld(request: Request):
    # print(request._query_params)
    auth_code = request._query_params['code']
    # HTTP/1.1 200
# Content-Type: application/json
# {
#   "access_token": "WIYLON2QSubLYyNcScIF5IPXf4iu6seioZYbCpxWHG4",
#   "token_type": "Bearer",
#   "expires_in": 7200,
#   "scope": "openid email",
#   "created_at": 1690193544,
#   "id_token": "eyJraWQiOiJ2NUluc184NVJIZk9Ydk1NSjFQZXFkanl2LW85OENtT05NaEF0b1YwY3RJIiwiYWxnIjoiUlMyNTYifQ.eyJpc3MiOiJwcmVzc2luZ2x5Iiwic3ViIjoiZDkwYzRjNjMtYjAxMi00MTI3LWE3NjUtZGVlOTJkMTNlYTc5IiwiYXVkIjoieXFQVjhPSmtUWGkyTXBscy1JbmIyc3c5WWE0anJUWEhXUUhSdnVEOEJCQSIsImV4cCI6MTY5MDE5MzY2NCwi
# id_token: jwt
    url = 'https://pressingly-account.onrender.com/oauth/token'
    myobj = {
        'grant_type': "authorization_code",
        'client_id': OIDC_CLIENT_ID,
        'client_secret': OIDC_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URL,
        'code': auth_code
    }
    public_key = "v5Ins_85RHfOXvMMJ1Peqdjyv-o98CmONMhAtoV0ctI"
    print("query params", myobj)
    x = requests.post(url, json = myobj)
    response = x.json()
    print(x.json())
    id_token = response['id_token']
    access_token = 'Bearer ' + response['access_token']
    # print(access_token)
    userinfo_url = "https://pressingly-account.onrender.com/oauth/userinfo"
    headers = {'Authorization': access_token}
    y = requests.get(userinfo_url, headers=headers)
    auth_email = y.json()['email']
    header, payload, signature = id_token.split('.')
    decoded_payload = jwt.utils.base64url_decode(payload)
    decoded_payload = decoded_payload.decode('utf8').replace("'", '"')

    response = RedirectResponse("/")
    # response = JSONResponse(content={"hello": response, "payload": decoded_payload, "userinfo": y.json()})
    response.set_cookie(key="auth_email", value=auth_email)
    return response


chainlit_route = app.router.routes
root_route = chainlit_route[-1]
chainlit_route.insert(-4, root_route)
chainlit_route.pop()

hello_route = chainlit_route[-1]
chainlit_route.insert(-4, hello_route)
chainlit_route.pop()


for route in app.router.routes:
    print(route)

from setup import search_agent
from utils import create_pdf_agent, process_response


# The search tool has no async implementation, we fall back to sync
# Agent is loaded before rendering
# @cl.langchain_factory(use_async=False)
# def factory():
#     return search_agent

# from urllib2 import Request, build_opener, HTTPCookieProcessor, HTTPHandler
# import cookielib

# #Create a CookieJar object to hold the cookies
# cj = cookielib.CookieJar()

# #Create an opener to open pages using the http protocol and to process cookies.
# opener = build_opener(HTTPCookieProcessor(cj), HTTPHandler())

# response = opener.open('https://57d7-222-252-20-227.ngrok-free.app/') # <---
# response.read()

from chainlit.session import sessions_sid, sessions_id

@cl.on_chat_start
async def start():
    # Always default to search mode
    cl.user_session.set("pdf_mode", False)

    # Sending an action button within a chatbot message
    actions = [
        cl.Action(
            name="pdf_mode", value="False", label="PDF reader", description="Click me!"
        ),
        cl.Action(
            name="login", value="False", label="Login", description="Click me!"
        )
    ]
    cl.user_session.set("search_agent", search_agent)

    email = cl.user_session.get('auth_email')
    print("auth_email", email)
    await cl.Message(
        content=str(email)+" Press this button to switch to chat mode with PDF reader. Open a new chat to reset mode.\nOtherwise, continue to chat for search mode.",
        actions=actions,
    ).send()

@cl.on_message
async def main(message: str):
    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("search_agent")  # type: LLMChain

    # Call the chain asynchronously
    res = await llm_chain.acall(message, callbacks=[cl.AsyncLangchainCallbackHandler()])

    # Do any post processing here

    # Send the response
    await cl.Message(content=res["text"]).send()

import webbrowser

@cl.action_callback("login")
async def on_action(action):
    webbrowser.open(login)


@cl.action_callback("pdf_mode")
async def on_action(action):
    # On button click, change to PDF reader mode
    await cl.Message(content="Entering PDF reader mode...").send()

    # Save user mode choice to session
    cl.user_session.set("pdf_mode", True)

    # Save PDF reader agent to session
    agent = await create_pdf_agent()
    cl.user_session.set("pdf_agent", agent)
    await action.remove()


# @cl.langchain_run
# async def run(agent, input):
#     pdf_mode = cl.user_session.get("pdf_mode")

#     if pdf_mode:
#         # PDF reader mode
#         agent = cl.user_session.get("pdf_agent")
#         res = await agent.acall(input, callbacks=[cl.AsyncLangchainCallbackHandler()])
#         await process_response(res)
#         return

#     # Search mode
#     res = await cl.make_async(agent)(input, callbacks=[cl.LangchainCallbackHandler()])
#     await cl.Message(content=res["output"]).send()
