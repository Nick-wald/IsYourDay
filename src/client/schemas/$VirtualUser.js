export const $VirtualUser = {
    description: `Virtual user model for isyourday project. `,
    properties: {
        id: {
            type: 'string',
            description: `Unique identifier for the virtual user`,
            format: 'uuid',
        },
        real_name: {
            type: 'string',
            description: `Real name of the virtual user`,
            isRequired: true,
        },
        sex: {
            type: 'number',
            description: `0 is unknown, 1 is man, 2 is woman`,
        },
        birthday: {
            type: 'any-of',
            description: `Birthday of the virtual user, default is 20 years ago`,
            contains: [{
                    type: 'string',
                    format: 'date-time',
                }, {
                    type: 'null',
                }],
        },
        tel: {
            type: 'any-of',
            description: `Telephone number of the virtual user`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        prompt: {
            type: 'any-of',
            description: `Prompt for the virtual user, used in AI interactions`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        location: {
            type: 'any-of',
            description: `Location of the virtual user`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        QQ: {
            type: 'any-of',
            description: `QQ number of the virtual user`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        wechat: {
            type: 'any-of',
            description: `WeChat ID of the virtual user`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        identify: {
            type: 'any-of',
            description: `Identification information of the virtual user`,
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        is_active: {
            type: 'boolean',
            description: `Indicates if the virtual user is active`,
        },
        email: {
            type: 'string',
            description: `Email address of the virtual user`,
            isRequired: true,
        },
        updated_at: {
            type: 'string',
            description: `Timestamp when the virtual user was last updated`,
            format: 'date-time',
        },
        created_at: {
            type: 'string',
            description: `Timestamp when the virtual user was created`,
            format: 'date-time',
        },
    },
};
//# sourceMappingURL=$VirtualUser.js.map