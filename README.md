# dualbot
a chat bot integrated with search mode and pdf file reader mode

[Demo](https://dualbot-image-7tzprwbq4a-as.a.run.app/)

## Why
GPT3 stopped training after early 2022, so it is not updated with new information. Using search engines allow the bot to answer questions about current events.
Reading PDF files is a plugin that I like but can't use without GPT4.

## How
- Integrate search engines using SerpAPI
_Reference_: [MRKL](https://docs.chainlit.io/examples/mrkl)
- Integrate PDF reading using Pinecone to store document and Faiss (?) to efficiently search documents
_Reference_: [Document QA](https://docs.chainlit.io/examples/qa) (not applicable, can't install `Chromadb`), [PDF-QA](https://github.com/Chainlit/cookbook/tree/main/pdf-qa)

## Demo
[Link to Demo video](https://www.loom.com/share/f90d9bc572e749b9b0447b593d387a98?sid=463258e5-22bf-4589-a4be-83558c09b4c9)
Correction: GPT3 stopped training after early 2022

## Bug

- [x] PDF reader bot is implemented in `langchain_run`, so it is regenerated for each new message. Fixed by:
    - Create a pdf chain immediately after user choose PDF reader mode
    - Save pdf chain to `user_session`
- [x] LangChain object is created once, so I have to figure a way to switch between search chain and pdf-reading chain. Fixed by:
    - Initialize search chain in `langchain_factory` and overwriting pdf-reading chain in `langchain_run`
    - Save user choice in `user_session`
