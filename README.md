# Hanzi Xiangqin | 汉字相亲
### A Chinese character "dating" game. 

A full stack web application for testing your knowledge of Chinese characters. It estimates how many characters you know by showing you a set of characters one at a time, requiring you to swipe right or left depending on whether you know the shown character or not. Inspired by the late `https://hanzitest.ericjiang.com` which the loss of inspired me to start this project, and to some extent by `http://hanzishan.com`.

Consists of 3 main services:
- hx-api - FastAPI-based backend API server
- hx-worker - backend python worker for running character tests
- hx-ui - frontend NextJS UI server

Also consists of database services:
- redis

Currently these can only be deployed locally via docker compose, however since everything is containerised with development/production ready images, it should be fairly simple to deploy in the cloud, depending on the setup you go for (Kubernetes, lambdas, ecs etc.) with some DNS setup too. The backend services have been designed to be horizontally scalable.
