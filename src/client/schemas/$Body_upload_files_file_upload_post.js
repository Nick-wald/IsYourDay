export const $Body_upload_files_file_upload_post = {
    properties: {
        files: {
            type: 'array',
            contains: {
                type: 'binary',
                format: 'binary',
            },
            isRequired: true,
        },
        is_public: {
            type: 'boolean',
            description: `是否公开文件`,
        },
        use_streaming: {
            type: 'boolean',
            description: `是否使用流式处理（推荐大文件使用）`,
        },
    },
};
//# sourceMappingURL=$Body_upload_files_file_upload_post.js.map