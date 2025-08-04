

/**
 * Event model for isyourday project. 
 */
export type Event = {
	/**
	 * Unique identifier for the event
	 */
	id?: string;
	/**
	 * ID of the virtual user associated with the event
	 */
	user_id: string;
	/**
	 * Title of the event
	 */
	title: string;
	/**
	 * Description of the event
	 */
	description?: string | null;
	/**
	 * Prompt for the event, used in AI interactions
	 */
	prompt?: string | null;
	/**
	 * Start time of the event
	 */
	start_time?: string | null;
	/**
	 * End time of the event, if applicable
	 */
	end_time?: string | null;
	/**
	 * Timestamp when the event was created
	 */
	created_at?: string;
};

