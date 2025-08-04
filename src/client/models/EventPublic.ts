

/**
 * Data model for creating a new event. 
 */
export type EventPublic = {
	title: string;
	description?: string | null;
	prompt?: string | null;
	start_time?: string | null;
	end_time?: string | null;
};

