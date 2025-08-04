import type { Body_login_for_access_token_auth_login_post } from '../models/Body_login_for_access_token_auth_login_post';
import type { Body_register_user_auth_register_post } from '../models/Body_register_user_auth_register_post';
import type { Body_send_email_endpoint_auth_send_email_post } from '../models/Body_send_email_endpoint_auth_send_email_post';
import type { Token } from '../models/Token';
import type { UserPublic } from '../models/UserPublic';
import type { UserSearchRole } from '../models/UserSearchRole';
import type { UserUpdate } from '../models/UserUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export type TDataGetAllUsersAuthUsersGet = {
                limit?: number
skip?: number
            }
export type TDataSearchUserAuthSearchGet = {
                limit?: number
/**
 * 搜索关键词
 */
q: string
skip?: number
            }
export type TDataGetUserByUsernameAuthProfileUserSearchRoleUserSearchValueGet = {
                userSearchRole: UserSearchRole
userSearchValue: string
            }
export type TDataRegisterUserAuthRegisterPost = {
                formData: Body_register_user_auth_register_post
            }
export type TDataLoginForAccessTokenAuthLoginPost = {
                formData: Body_login_for_access_token_auth_login_post
            }
export type TDataSendEmailEndpointAuthSendEmailPost = {
                formData: Body_send_email_endpoint_auth_send_email_post
            }
export type TDataUpdateUserBasicInfoAuthUpdatePatch = {
                requestBody: UserUpdate
userPk?: string | null
            }

export class 登录鉴权Service {

	/**
	 * 获取用户列表
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static getAllUsersAuthUsersGet(data: TDataGetAllUsersAuthUsersGet = {}): CancelablePromise<Array<UserPublic>> {
		const {
limit = 10,
skip = 0,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/auth/users',
			query: {
				skip, limit
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 获取登录态用户信息
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static getCurrentUserAuthMeGet(): CancelablePromise<UserPublic> {
				return __request(OpenAPI, {
			method: 'GET',
			url: '/auth/me',
		});
	}

	/**
	 * 搜索用户
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static searchUserAuthSearchGet(data: TDataSearchUserAuthSearchGet): CancelablePromise<Array<UserPublic>> {
		const {
limit = 10,
q,
skip = 0,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/auth/search',
			query: {
				q, skip, limit
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 获取用户信息
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static getUserByUsernameAuthProfileUserSearchRoleUserSearchValueGet(data: TDataGetUserByUsernameAuthProfileUserSearchRoleUserSearchValueGet): CancelablePromise<UserPublic> {
		const {
userSearchRole,
userSearchValue,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/auth/profile/{user_search_role}/{user_search_value}',
			path: {
				user_search_role: userSearchRole, user_search_value: userSearchValue
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 用户注册
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static registerUserAuthRegisterPost(data: TDataRegisterUserAuthRegisterPost): CancelablePromise<UserPublic> {
		const {
formData,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/auth/register',
			formData: formData,
			mediaType: 'application/x-www-form-urlencoded',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 用户登录
	 * @returns Token Successful Response
	 * @throws ApiError
	 */
	public static loginForAccessTokenAuthLoginPost(data: TDataLoginForAccessTokenAuthLoginPost): CancelablePromise<Token> {
		const {
formData,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/auth/login',
			formData: formData,
			mediaType: 'application/x-www-form-urlencoded',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 邮件发送接口
	 * files是用户上传的文件列表，files_in_store是已存储在服务器上的文件ID列表（注意需要权限）。
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static sendEmailEndpointAuthSendEmailPost(data: TDataSendEmailEndpointAuthSendEmailPost): CancelablePromise<unknown> {
		const {
formData,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/auth/send-email',
			formData: formData,
			mediaType: 'multipart/form-data',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 更新用户信息
	 * @returns UserPublic Successful Response
	 * @throws ApiError
	 */
	public static updateUserBasicInfoAuthUpdatePatch(data: TDataUpdateUserBasicInfoAuthUpdatePatch): CancelablePromise<UserPublic> {
		const {
requestBody,
userPk,
} = data;
		return __request(OpenAPI, {
			method: 'PATCH',
			url: '/auth/update',
			query: {
				user_pk: userPk
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

}