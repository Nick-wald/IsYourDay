export const $Body_send_email_endpoint_auth_send_email_post = {
	properties: {
		receiver: {
	type: 'array',
	contains: {
	type: 'string',
	format: 'uuid',
},
	isRequired: true,
},
		subject: {
	type: 'string',
	description: `邮件主题`,
	minLength: 1,
},
		content: {
	type: 'string',
	description: `邮件内容（支持HTML）`,
	minLength: 1,
},
		files: {
	type: 'any-of',
	contains: [{
	type: 'array',
	contains: {
	type: 'binary',
	format: 'binary',
},
}, {
	type: 'null',
}],
},
		files_in_store: {
	type: 'any-of',
	contains: [{
	type: 'array',
	contains: {
	type: 'string',
	format: 'uuid',
},
}, {
	type: 'null',
}],
},
		store_upload_files: {
	type: 'boolean',
	description: `是否存储上传的文件到服务器`,
},
	},
} as const;