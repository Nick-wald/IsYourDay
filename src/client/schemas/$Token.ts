export const $Token = {
	description: `Token model for user authentication.`,
	properties: {
		access_token: {
	type: 'string',
	isRequired: true,
},
		token_type: {
	type: 'string',
},
	},
} as const;