export const $Body_update_file_info_file__file_id__patch = {
	properties: {
		name: {
	type: 'any-of',
	description: `新文件名`,
	contains: [{
	type: 'string',
}, {
	type: 'null',
}],
},
		is_public: {
	type: 'any-of',
	description: `是否公开`,
	contains: [{
	type: 'boolean',
}, {
	type: 'null',
}],
},
	},
} as const;