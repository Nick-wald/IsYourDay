export const $FileDB = {
    description: `File model for storing file metadata.`,
    properties: {
        id: {
            type: 'string',
            description: `Unique identifier for the file`,
            format: 'uuid',
        },
        name: {
            type: 'string',
            description: `Name of the file`,
            isRequired: true,
        },
        md5: {
            type: 'string',
            description: `MD5 hash of the file for integrity check`,
            isRequired: true,
        },
        is_public: {
            type: 'boolean',
            description: `Is the file publicly accessible?`,
        },
        path: {
            type: 'string',
            description: `Path to the file on the server`,
            isRequired: true,
        },
        size: {
            type: 'number',
            description: `Size of the file in bytes`,
        },
        uploader_id: {
            type: 'any-of',
            description: `ID of the user who uploaded the file`,
            contains: [{
                    type: 'string',
                    format: 'uuid',
                }, {
                    type: 'null',
                }],
            isRequired: true,
        },
        upload_time: {
            type: 'string',
            description: `Timestamp when the file was uploaded`,
            format: 'date-time',
        },
    },
};
//# sourceMappingURL=$FileDB.js.map