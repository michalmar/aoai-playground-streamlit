# aoai-simple-playground


## Deployment
1. create Web App in Azure with link to this repo to activate GHA deployment
2. configure app startup command: `python -m streamlit run home.py --server.port 8000 --server.address 0.0.0.0`
3. confuigure app env variables:
```shell
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_API_VERSION=2024-04-01-preview
AZURE_OPENAI_MODELS_DEPLOYEMNTS=deployment1,deployment2
```


## Example of playgrounds
### Example of Chat playground

![Example of Chat playground](docs/chat-playground.png)

### Example of Completion playground
![Example of Completion playground](docs/completion-playground.png)