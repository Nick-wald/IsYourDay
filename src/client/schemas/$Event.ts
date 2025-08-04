export const $Event = {
	description: `Event model for isyourday project. `,
	properties: {
		id: {
	type: 'string',
	description: `Unique identifier for the event`,
	format: 'uuid',
},
		user_id: {
	type: 'string',
	description: `ID of the virtual user associated with the event`,
	isRequired: true,
	format: 'uuid',
},
		title: {
	type: 'string',
	description: `Title of the event`,
	isRequired: true,
},
		description: {
	type: 'any-of',
	description: `Description of the event`,
	contains: [{
	type: 'string',
}, {
	type: 'null',
}],
},
		prompt: {
	type: 'any-of',
	description: `Prompt for the event, used in AI interactions`,
	contains: [{
	type: 'string',
}, {
	type: 'null',
}],
},
		start_time: {
	type: 'any-of',
	description: `Start time of the event`,
	contains: [{
	type: 'string',
	format: 'date-time',
}, {
	type: 'null',
}],
},
		end_time: {
	type: 'any-of',
	description: `End time of the event, if applicable`,
	contains: [{
	type: 'string',
	format: 'date-time',
}, {
	type: 'null',
}],
},
		created_at: {
	type: 'string',
	description: `Timestamp when the event was created`,
	format: 'date-time',
},
	},
} as const;