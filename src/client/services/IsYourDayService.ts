import type { Event } from '../models/Event';
import type { EventPublic } from '../models/EventPublic';
import type { VirtualUser } from '../models/VirtualUser';
import type { VirtualUserPublic } from '../models/VirtualUserPublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export type TDataGetVirtualUsersIsyourdayUsersGet = {
                limit?: number
skip?: number
            }
export type TDataGetVirtualUserIsyourdayUserUserIdGet = {
                userId: string
            }
export type TDataUpdateVirtualUserIsyourdayUserUserIdPatch = {
                requestBody: VirtualUserPublic
userId: string
            }
export type TDataCreateVirtualUserIsyourdayUserPost = {
                requestBody: VirtualUserPublic
            }
export type TDataSearchVirtualUsersIsyourdayUsersSearchGet = {
                query?: string | null
            }
export type TDataDeleteVirtualUserIsyourdayUsersBatchDelete = {
                requestBody: Array<string>
            }
export type TDataGetUserEventsIsyourdayUserUserIdEventsGet = {
                userId: string
            }
export type TDataCreateUserEventIsyourdayUserUserIdEventsPost = {
                requestBody: EventPublic
userId: string
            }
export type TDataDeleteUserEventsIsyourdayUserUserIdEventsBatchDelete = {
                requestBody: Array<string>
userId: string
            }
export type TDataUpdateUserEventIsyourdayUserUserIdEventEventIdPatch = {
                eventId: string
requestBody: EventPublic
userId: string
            }

export class IsYourDayService {

	/**
	 * 获取虚拟用户列表
	 * 获取虚拟用户列表
	 * @returns VirtualUser Successful Response
	 * @throws ApiError
	 */
	public static getVirtualUsersIsyourdayUsersGet(data: TDataGetVirtualUsersIsyourdayUsersGet = {}): CancelablePromise<Array<VirtualUser>> {
		const {
limit = 10,
skip = 0,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/isyourday/users',
			query: {
				skip, limit
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 获取单个虚拟用户
	 * 根据ID获取单个虚拟用户
	 * @returns VirtualUser Successful Response
	 * @throws ApiError
	 */
	public static getVirtualUserIsyourdayUserUserIdGet(data: TDataGetVirtualUserIsyourdayUserUserIdGet): CancelablePromise<VirtualUser> {
		const {
userId,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/isyourday/user/{user_id}',
			path: {
				user_id: userId
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 更新虚拟用户
	 * 更新虚拟用户信息
	 * @returns VirtualUser Successful Response
	 * @throws ApiError
	 */
	public static updateVirtualUserIsyourdayUserUserIdPatch(data: TDataUpdateVirtualUserIsyourdayUserUserIdPatch): CancelablePromise<VirtualUser> {
		const {
requestBody,
userId,
} = data;
		return __request(OpenAPI, {
			method: 'PATCH',
			url: '/isyourday/user/{user_id}',
			path: {
				user_id: userId
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 创建虚拟用户
	 * 创建新的虚拟用户
	 * @returns VirtualUser Successful Response
	 * @throws ApiError
	 */
	public static createVirtualUserIsyourdayUserPost(data: TDataCreateVirtualUserIsyourdayUserPost): CancelablePromise<VirtualUser> {
		const {
requestBody,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/isyourday/user',
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 搜索虚拟用户
	 * 搜索虚拟用户
	 * @returns VirtualUser Successful Response
	 * @throws ApiError
	 */
	public static searchVirtualUsersIsyourdayUsersSearchGet(data: TDataSearchVirtualUsersIsyourdayUsersSearchGet = {}): CancelablePromise<Array<VirtualUser>> {
		const {
query,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/isyourday/users/search',
			query: {
				query
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 批量删除删除虚拟用户
	 * 删除虚拟用户
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static deleteVirtualUserIsyourdayUsersBatchDelete(data: TDataDeleteVirtualUserIsyourdayUsersBatchDelete): CancelablePromise<Record<string, unknown>> {
		const {
requestBody,
} = data;
		return __request(OpenAPI, {
			method: 'DELETE',
			url: '/isyourday/users/batch',
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 获取用户事件列表
	 * 获取指定用户的事件列表
	 * @returns Event Successful Response
	 * @throws ApiError
	 */
	public static getUserEventsIsyourdayUserUserIdEventsGet(data: TDataGetUserEventsIsyourdayUserUserIdEventsGet): CancelablePromise<Array<Event>> {
		const {
userId,
} = data;
		return __request(OpenAPI, {
			method: 'GET',
			url: '/isyourday/user/{user_id}/events',
			path: {
				user_id: userId
			},
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 创建用户事件
	 * 为指定用户创建事件
	 * @returns Event Successful Response
	 * @throws ApiError
	 */
	public static createUserEventIsyourdayUserUserIdEventsPost(data: TDataCreateUserEventIsyourdayUserUserIdEventsPost): CancelablePromise<Event> {
		const {
requestBody,
userId,
} = data;
		return __request(OpenAPI, {
			method: 'POST',
			url: '/isyourday/user/{user_id}/events',
			path: {
				user_id: userId
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 批量删除用户事件
	 * 批量删除指定用户的事件
	 * @returns unknown Successful Response
	 * @throws ApiError
	 */
	public static deleteUserEventsIsyourdayUserUserIdEventsBatchDelete(data: TDataDeleteUserEventsIsyourdayUserUserIdEventsBatchDelete): CancelablePromise<Record<string, unknown>> {
		const {
requestBody,
userId,
} = data;
		return __request(OpenAPI, {
			method: 'DELETE',
			url: '/isyourday/user/{user_id}/events/batch',
			path: {
				user_id: userId
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

	/**
	 * 更新用户事件详情
	 * 更新指定用户的事件
	 * @returns Event Successful Response
	 * @throws ApiError
	 */
	public static updateUserEventIsyourdayUserUserIdEventEventIdPatch(data: TDataUpdateUserEventIsyourdayUserUserIdEventEventIdPatch): CancelablePromise<Event> {
		const {
eventId,
requestBody,
userId,
} = data;
		return __request(OpenAPI, {
			method: 'PATCH',
			url: '/isyourday/user/{user_id}/event/{event_id}',
			path: {
				user_id: userId, event_id: eventId
			},
			body: requestBody,
			mediaType: 'application/json',
			errors: {
				422: `Validation Error`,
			},
		});
	}

}