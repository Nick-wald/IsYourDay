export const $VirtualUserPublic = {
    description: `Data model for creating a new virtual user. `,
    properties: {
        real_name: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        sex: {
            type: 'number',
        },
        birthday: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                    format: 'date-time',
                }, {
                    type: 'null',
                }],
        },
        tel: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        prompt: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        location: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        QQ: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        wechat: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        identify: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                }, {
                    type: 'null',
                }],
        },
        email: {
            type: 'string',
            isRequired: true,
        },
    },
};
//# sourceMappingURL=$VirtualUserPublic.js.map