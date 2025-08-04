export const $EventPublic = {
    description: `Data model for creating a new event. `,
    properties: {
        title: {
            type: 'string',
            isRequired: true,
        },
        description: {
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
        start_time: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                    format: 'date-time',
                }, {
                    type: 'null',
                }],
        },
        end_time: {
            type: 'any-of',
            contains: [{
                    type: 'string',
                    format: 'date-time',
                }, {
                    type: 'null',
                }],
        },
    },
};
//# sourceMappingURL=$EventPublic.js.map