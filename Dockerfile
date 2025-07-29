FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy code
COPY . /app

# Install deps
RUN pip install --no-cache-dir -r python-libs.txt

# Use Tornado app filename passed as build ARG
ARG APP=listing_service.py
ENV APP=$APP

EXPOSE 8000

CMD ["sh", "-c", "python $APP --port=8000 --debug=false"]