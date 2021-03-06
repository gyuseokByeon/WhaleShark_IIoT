/*
 * networkmanager.h
 *
 */
#include <common/smsgdef.h>

#ifndef NETWORK_NETWORKMANAGER_H_
#define NETWORK_NETWORKMANAGER_H_

#define SMSG_WIFI_OK					0x00000001 // Wifi OK
#define SMSG_WIFI_ERROR					0x00000002 // Wifi Error
#define SMSG_WIFI_FAIL					0x00000003 // Wifi Fail
#define SMSG_WIFI_TIMEOUT				0x00000004 // Wifi Timeout
#define SMSG_TCP_SEND_DATA				0x00000005 // TCP Send Data

typedef enum
{
	STATUS_NONE,
	STATUS_WIFI_RESTART,
	STATUS_ECHO_OFF,
	STATUS_SET_RFPOWER,
	STATUS_DISABLE_SLEEP_MODE,
	STATUS_CHECK_WIFI_MODE,
	STATUS_GET_WIFI_MODE,
	STATUS_SET_WIFI_MODE,
	STATUS_CONNECT_WIFI,
	STATUS_SET_DHCP,
	STATUS_QUERY_DHCP_INFO,
	STATUS_GET_DHCP_INFO,
	STATUS_QUERY_AP_INFO,
	STATUS_GET_AP_INFO,
	STATUS_SET_LOCAL_INFO,
	STATUS_QUERY_LOCAL_INFO,
	STATUS_GET_LOCAL_INFO,
	STATUS_DISCONNECT_WIFI,
	STATUS_TCP_CONNECT,
	STATUS_SET_SEND_DATA_LENGTH,
	STATUS_READY_TO_SEND_DATA,
	STATUS_SEND_DATA,
	STATUS_WAIT_ACK,
	STATUS_STANDBY_SEND,
	STATUS_CONTINUOUS_SEND,
	STATUS_QUERY_MAC_INFO,
	STATUS_GET_MAC_INFO,
	STATUS_SET_MAC_INFO,
	STATUS_RECEIVE_DATA,
	STATUS_TCP_DISCONNECT,
	STATUS_MAX
}NetworkStatus;

typedef struct _NetworkInfoData {
	rt_uint8_t response;
	NetworkStatus networkStatus;

	rt_uint8_t data[128];
} NetworkInfoData;

rt_bool_t InitNetworkManager(void);
void NetworkMangerSendMessage(MqData_t *pMqData);
rt_bool_t StartNetworkManager(void);
void SendData(rt_uint8_t *pData, rt_size_t dataSize);

#endif /* NETWORK_NETWORKMANAGER_H_ */
