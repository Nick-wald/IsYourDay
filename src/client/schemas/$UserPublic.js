export const $UserPublic = {
    description: `Public user model for API responses.`,
    properties: {
        id: {
            type: 'string',
            isRequired: true,
            format: 'uuid',
        },
        username: {
            type: 'string',
            isRequired: true,
        },
        email: {
            type: 'string',
            isRequired: true,
        },
        active: {
            type: 'boolean',
            isRequired: true,
        },
    },
};
//# sourceMappingURL=$UserPublic.js.map