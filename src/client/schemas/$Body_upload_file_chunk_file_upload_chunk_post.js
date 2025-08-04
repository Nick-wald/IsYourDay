export const $Body_upload_file_chunk_file_upload_chunk_post = {
    properties: {
        file: {
            type: 'binary',
            isRequired: true,
            format: 'binary',
        },
        chunk_index: {
            type: 'number',
            description: `分片索引（从0开始）`,
            isRequired: true,
        },
        total_chunks: {
            type: 'number',
            description: `总分片数`,
            isRequired: true,
        },
        file_id: {
            type: 'string',
            description: `文件唯一标识符`,
            isRequired: true,
        },
        original_filename: {
            type: 'string',
            description: `原始文件名`,
            isRequired: true,
        },
        total_size: {
            type: 'number',
            description: `文件总大小`,
            isRequired: true,
        },
        is_public: {
            type: 'boolean',
            description: `是否公开文件`,
        },
    },
};
//# sourceMappingURL=$Body_upload_file_chunk_file_upload_chunk_post.js.map