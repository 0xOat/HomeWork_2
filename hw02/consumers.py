from channels.generic.websocket import AsyncWebsocketConsumer
import json
from clickhouse_connect import get_client

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        client = get_client(host='localhost')
        result = client.query('SELECT count() FROM events')
        await self.send(text_data=json.dumps({'count': result.result_rows[0][0]}))