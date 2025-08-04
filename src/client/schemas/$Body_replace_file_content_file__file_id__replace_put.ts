export const $Body_replace_file_content_file__file_id__replace_put = {
	properties: {
		new_file: {
	type: 'binary',
	isRequired: true,
	format: 'binary',
},
		use_streaming: {
	type: 'boolean',
	description: `是否使用流式处理`,
},
	},
} as const;