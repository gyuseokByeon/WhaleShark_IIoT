import unittest

import asyncio
import socket
import logging
import redis
import yaml
import sys
import json
import pika

from net_socket.iiot_tcp_async_server import AsyncServer

logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)

"""
grafana docker
docker run -d -p 3000:3000 grafana/grafana

influxdb
step1 : docker pull influxdb
step2 :
docker run -p 8086:8086 -v $PROJECT_PATH/WhaleShark_IIoT/config:/var/lib/influxdb influxdb -config /var/lib/influxdb/influxdb.conf -e INFLUXDB_ADMIN_USER=whaleshark -e INFLUXDB_ADMIN_PASSWORD=whaleshark
Please refer https://www.open-plant.com/knowledge-base/how-to-install-influxdb-docker-for-windows-10/
"""


class tcp_server:

	def __init__(self:  'tcp_server') -> 'tcp_server':
		with open('config/config_server_develop.yaml','r') as file:
			config_obj=yaml.load(file,Loader=yaml.FullLoader)
			self.tcp_host=config_obj['iiot_server']['tcp_server']['ip_address']
			self.tcp_port=config_obj['iiot_server']['tcp_server']['port']

			self.redis_host=config_obj['iiot_server']['redis_server']['ip_address']
			self.redis_port=config_obj['iiot_server']['redis_server']['port']

			self.rabbitmq_host=config_obj['iiot_server']['rabbit_mq']['ip_address']
			self.rabbitmq_port=config_obj['iiot_server']['rabbit_mq']['port']

	def connect_redis(self,host,port):
		"""
		Get connector for redis
		If you don't have redis, you can use redis on docker with follow steps.
		Getting most recent redis image
		shell: docker pull redis

		docker pull redis
		docker run --name whaleshark-redis -d -p 6379:6379 redis
		docker run -it --link whaleshark-redis:redis --rm redis redis-cli -h redis -p 6379

		:param host: redis access host ip
		:param port: redis access port
		:return: redis connector
		"""
		redis_obj=None
		try:
			conn_params={
				"host":host,
				"port":port,
			}
			redis_obj=redis.StrictRedis(**conn_params)

		except Exception as e:
			logging.error(str(e))

		return redis_obj

	def config_equip_desc(self,address,port,init=False):
		'''
		Configure redis for equipment sensor desc(sensor_cd)
		key : const sensor_cd
		value : dictionary or map has sensor_cd:sensor description
		:return: redis connector
		'''
		redis_con=None
		try:
			redis_con=self.connect_redis(address,port)
			facilities_dict=redis_con.get('facilities_info')

			if facilities_dict==None:
				facilities_dict={'TS0001':{
					'0001':'TS_VOLT1_(RS)',
					'0002':'TS_VOLT1_(ST)',
					'0003':'TS_VOLT1_(RT)',
					'0004':'TS_AMP1_(R)',
					'0005':'TS_AMP1_(S)',
					'0006':'TS_AMP1_(T)',
					'0007':'INNER_PRESS',
					'0008':'PUMP_PRESS',
					'0009':'TEMPERATURE1',
					'0010':'OVER_TEMP'
				}
				}
				redis_con.set('facilities_info',json.dumps(facilities_dict))
			else:
				if init==True:
					redis_con.delete('facilities_info')

		except Exception as e:
			logging.error(str(e))

		return redis_con

	def get_messagequeue(self,address,port):
		'''
		If you don't have rabbitmq, you can use docker.
		docker run -d --hostname whaleshark --name whaleshark-rabbit -p 5672:5672 -p 8080:15672 -e RABBITMQ_DEFAULT_USER=whaleshark -e RABBITMQ_DEFAULT_PASS=whaleshark rabbitmq:3-management

		get message queue connector (rabbit mq) with address, port
		:param address: rabbit mq server ip
		:param port: rabbitmq server port(AMQP)
		:return: rabbitmq connection channel
		'''
		channel=None
		try:
			credentials=pika.PlainCredentials('whaleshark','whaleshark')
			param=pika.ConnectionParameters(address,port,'/',credentials)
			connection=pika.BlockingConnection(param)
			channel=connection.channel()
			channel.exchange_declare(exchange='facility',exchange_type='fanout')
		except Exception as e:
			logging.exception(str(e))

		return channel

	def init_config(self):
		self.redis_con=self.config_equip_desc(address=self.redis_host,port=self.redis_port)
		if self.redis_con==None:
			logging.error('redis configuration fail')
			sys.exit()

		self.mq_channel=self.get_messagequeue(address=self.rabbitmq_host,port=self.rabbitmq_port)
		if self.mq_channel==None:
			logging.error('rabbitmq configuration fail')
			sys.exit()


	def get_redis_con(self):
		return self.redis_con


	def get_mq_channel(self):
		return self.mq_channel


	def get_server_socket(self):
		server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		server_socket.setblocking(0)
		server_socket.bind(('',self.tcp_port))
		server_socket.listen(1)
		logging.debug('IIoT Client Ready ({ip}:{port})'.format(ip=self.tcp_host,port=self.tcp_port))
		return server_socket


if __name__=='__main__':
	try:
		server=tcp_server()
		server.init_config()
		redis_con=server.get_redis_con()
		mq_channel=server.get_mq_channel()
		server_socket=server.get_server_socket()
		msg_size=27
		async_server=AsyncServer()
		event_manger=asyncio.get_event_loop()
		event_manger.run_until_complete(
			async_server.get_client(event_manger,server_socket,msg_size,redis_con,mq_channel))

	except Exception as e:
		print(str(e))


