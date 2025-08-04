export const $Body_login_for_access_token_auth_login_post = {
    properties: {
        grant_type: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                    pattern: '^password$',
                }, {
                    type: 'null',
                }],
        },
        username: {
            type: 'string',
            isRequired: true,
        },
        password: {
            type: 'string',
            isRequired: true,
            format: 'password',
        },
        scope: {
            type: 'string',
        },
        client_id: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        client_secret: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
    },
};
//# sourceMappingURL=$Body_login_for_access_token_auth_login_post.js.map