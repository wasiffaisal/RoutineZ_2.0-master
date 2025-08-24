#!/bin/bash

# Install backend dependencies
cd api
pip install -r requirements.txt

# Install frontend dependencies and build
cd ../USIS/usis-frontend
npm install
npm run build