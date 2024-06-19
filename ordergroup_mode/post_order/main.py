#!/usr/bin/env python

import config as c
import datetime
import csv
import time
import json
import requests
import logging

destination_url = f"http://{c.host}/wms/black/order/receive"

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST).strftime('%Y%m%d-%H%M%S')

logging.basicConfig(
    filename=f"log-{now}.txt",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :%(message)s",
    datefmt="%Y/%m/%dT%H:%M:%S+09:00"
)

def main():
    with open("log.txt", "w") as f:
        f.write("")
    logging.info("start...")

    try:
        pre_data = get_data()
        data = dict( data = format_data(pre_data))

        
        num_of_orders = len(data["data"])
        
        total_qty = 0
        for x in data["data"]:
            for y in x["details"]:
                total_qty += y["qty"]
        logging.info(f"{num_of_orders} orders/{total_qty} units")

        json_data = json.dumps(data, indent=2)
        res = requests.post(
            destination_url,
            json_data,
            headers={'Content-Type': 'application/json'},
            timeout=3.5
        )
        logging.info(f"post orders. {json_data}")
        logging.info(f"response: {res.json()}")


    except Exception as e:
        logging.error(e)

    finally:
        logging.info("complete.")


def format_data(pre_data):
    batch_id = str(int(time.time()))
    order_group_id = f"サンプル_{batch_id}"

    num_of_order_id = 1

    data = list()
    for x in pre_data:
        order_id = f"{batch_id}-{num_of_order_id}"
        order = {
            "orderGroupId": order_group_id,
            "orderId": order_id,
            "systemId": c.system_id,
            "type": "Normal",
            "wallId": f"{c.system_id}-WALL-{x[:3]}",
            "indexInWall": int(x.split("-")[2]),
            "needSerialNo": "false",
            "details": list(),
            "specifyBoxId": None,
            "specifyCartId": None,
            "cartDestination": None
        }
        number_of_order_defail_id = 1

        for y in pre_data[x]:
            order["details"].append(
                dict(
                    orderDetailId = f"{order_id}-{number_of_order_defail_id}",
                    productId = y,
                    productBarcode = y,
                    productName = y,
                    needSerialNo = None,
                    qty = pre_data[x][y]
                )
            )
            number_of_order_defail_id += 1
        data.append(order)
        num_of_order_id += 1
    
    return data

def get_data():
    data = dict()
    with open(c.orderfile) as f:
        for x in csv.reader(f):
            loc = f"{x[2]}-{x[3]}-{x[4]}"
            if loc in data.keys():
                if x[0] in data[loc].keys():
                    data[loc][x[0]] += int(x[1])
                else:
                    data[loc].setdefault(
                        x[0], int(x[1])
                    )
            
            else:
                data.setdefault(
                    loc,
                    {
                        x[0]: int(x[1])
                    }
                )
    
    return data


if __name__ == '__main__':
    main()

