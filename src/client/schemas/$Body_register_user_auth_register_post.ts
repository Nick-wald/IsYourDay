export const $Body_register_user_auth_register_post = {
	properties: {
		username: {
	type: 'string',
	description: `用户名`,
	isRequired: true,
},
		email: {
	type: 'string',
	description: `用户邮箱`,
	isRequired: true,
	pattern: '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$',
},
		password: {
	type: 'string',
	description: `用户密码`,
	isRequired: true,
},
	},
} as const;