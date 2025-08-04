import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class 登录鉴权Service {
    /**
     * 获取用户列表
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    static getAllUsersAuthUsersGet(data = {}) {
        const { limit = 10, skip = 0, } = data;
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
    static getCurrentUserAuthMeGet() {
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
    static searchUserAuthSearchGet(data) {
        const { limit = 10, q, skip = 0, } = data;
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
    static getUserByUsernameAuthProfileUserSearchRoleUserSearchValueGet(data) {
        const { userSearchRole, userSearchValue, } = data;
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
    static registerUserAuthRegisterPost(data) {
        const { formData, } = data;
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
    static loginForAccessTokenAuthLoginPost(data) {
        const { formData, } = data;
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
    static sendEmailEndpointAuthSendEmailPost(data) {
        const { formData, } = data;
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
    static updateUserBasicInfoAuthUpdatePatch(data) {
        const { requestBody, userPk, } = data;
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
//# sourceMappingURL=%E7%99%BB%E5%BD%95%E9%89%B4%E6%9D%83Service.js.map