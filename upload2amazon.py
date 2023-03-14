#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Upload2AmazonAppstore
@File    ：upload2amazon.py
@Author  ：Xiaoxuan Hao
@Date    ：2023/3/14 9:53
'''
import logging
import requests

class Upload2Amazon:

    client_id = "amzn1.application-oa2-client.a638c480f88e476d90601bb5254773fe"
    client_secret = "275a15e85365a8a6b384832173a8ff5005337218c3f8647792212516cc82df35"
    app_id = "amzn1.devportal.mobileapp.703658a665104b40b1d88acacc842f74"
    BASE_URL = 'https://developer.amazon.com/api/appstore'

    def auth2amazon(self):
        scope = "appstore::apps:readwrite"
        grant_type = "client_credentials"
        data = {
            "grant_type": grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": scope
        }
        amazon_auth_url = "https://api.amazon.com/auth/o2/token"
        auth_response = requests.post(amazon_auth_url, data=data)
        # 从身份验证响应中读取令牌
        auth_response_json = auth_response.json()
        auth_token = auth_response_json["access_token"]
        auth_token_header_value = "Bearer %s" % auth_token
        auth_token_header = {"Authorization": auth_token_header_value}
        logging.info("auth_token_header:{}".format(auth_token_header))
        return auth_token_header

    def get_edit_id(self):
        '''获取当前Edit的ID,edit状态必须为IN_PROGRESS才能上传apk'''
        get_edits_path = '/v1/applications/%s/edits' % self.app_id
        get_edits_url = self.BASE_URL + get_edits_path
        auth_token_header = self.auth2amazon()
        get_edits_response = requests.get(get_edits_url, headers=auth_token_header)
        # 如果返回的数据为空，则创建一个新的Edit
        if not get_edits_response.json():
            print("当前无edit，新建ing...")
            return self.create_new_edit()
        # 获取当前的Edit
        current_edit = get_edits_response.json()[0]
        edit_status = current_edit.get('status')
        # 如果当前Edit的状态是IN_PROGRESS，则返回ID,否则创建新的Edit
        if edit_status == 'IN_PROGRESS':
            logging.info("current_edit:{}",format(current_edit))
            return current_edit['id']
        else:
            print("当前edit状态为{}，无法上传apk，新建editing...".format(edit_status))
            return self.create_new_edit()

    def replace_exist_apk(self, apk_file_path):
        '''新建edit时会默认继承上一个版本的apk，此方法用于替换最新的apk到edit中'''
        ## 获取当前的APK列表
        get_apks_path = '/v1/applications/%s/edits/%s/apks' % (self.app_id, self.get_edit_id)
        get_apks_url = self.BASE_URL + get_apks_path
        auth_token_header = self.auth2amazon()
        apks = requests.get(get_apks_url, headers=auth_token_header)
        firstAPK = apks[0]
        apk_id = firstAPK['id']
        replace_apk_path = '/v1/applications/%s/edits/%s/apks/%s/replace' % (self.app_id, self.get_edit_id, apk_id)

        ##打开APK文件
        local_apk = open(local_apk_path, 'rb').read()
        replace_apk_url = self.BASE_URL + replace_apk_path
        all_headers = {
            'Content-Type': 'application/vnd.android.package-archive',
            'If-Match': etag
        }
        all_headers.update(auth_token_header)
        replace_apk_response = requests.put(replace_apk_url, headers=all_headers, data=local_apk)
        print('上传结果：{}'.format(replace_apk_response))

    def create_new_edit(self):
        '''新建edit'''
        create_edits_path = '/v1/applications/%s/edits' % self.app_id
        create_edits_url = self.BASE_URL + create_edits_path
        auth_token_header = self.auth2amazon()
        create_edits_response = requests.post(create_edits_url, headers=auth_token_header)
        current_edit = create_edits_response.json()
        edit_id = current_edit['id']
        return edit_id

if __name__ == '__main__':
    uploader = Upload2Amazon()
