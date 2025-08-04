import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class IsYourDayService {
    /**
     * 获取虚拟用户列表
     * 获取虚拟用户列表
     * @returns VirtualUser Successful Response
     * @throws ApiError
     */
    static getVirtualUsersIsyourdayUsersGet(data = {}) {
        const { limit = 10, skip = 0, } = data;
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
    static getVirtualUserIsyourdayUserUserIdGet(data) {
        const { userId, } = data;
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
    static updateVirtualUserIsyourdayUserUserIdPatch(data) {
        const { requestBody, userId, } = data;
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
    static createVirtualUserIsyourdayUserPost(data) {
        const { requestBody, } = data;
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
    static searchVirtualUsersIsyourdayUsersSearchGet(data = {}) {
        const { query, } = data;
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
    static deleteVirtualUserIsyourdayUsersBatchDelete(data) {
        const { requestBody, } = data;
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
    static getUserEventsIsyourdayUserUserIdEventsGet(data) {
        const { userId, } = data;
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
    static createUserEventIsyourdayUserUserIdEventsPost(data) {
        const { requestBody, userId, } = data;
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
    static deleteUserEventsIsyourdayUserUserIdEventsBatchDelete(data) {
        const { requestBody, userId, } = data;
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
    static updateUserEventIsyourdayUserUserIdEventEventIdPatch(data) {
        const { eventId, requestBody, userId, } = data;
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
//# sourceMappingURL=IsYourDayService.js.map