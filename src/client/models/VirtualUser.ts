

/**
 * Virtual user model for isyourday project. 
 */
export type VirtualUser = {
	/**
	 * Unique identifier for the virtual user
	 */
	id?: string;
	/**
	 * Real name of the virtual user
	 */
	real_name: string;
	/**
	 * 0 is unknown, 1 is man, 2 is woman
	 */
	sex?: number;
	/**
	 * Birthday of the virtual user, default is 20 years ago
	 */
	birthday?: string | null;
	/**
	 * Telephone number of the virtual user
	 */
	tel?: string | null;
	/**
	 * Prompt for the virtual user, used in AI interactions
	 */
	prompt?: string | null;
	/**
	 * Location of the virtual user
	 */
	location?: string | null;
	/**
	 * QQ number of the virtual user
	 */
	QQ?: string | null;
	/**
	 * WeChat ID of the virtual user
	 */
	wechat?: string | null;
	/**
	 * Identification information of the virtual user
	 */
	identify?: string | null;
	/**
	 * Indicates if the virtual user is active
	 */
	is_active?: boolean;
	/**
	 * Email address of the virtual user
	 */
	email: string;
	/**
	 * Timestamp when the virtual user was last updated
	 */
	updated_at?: string;
	/**
	 * Timestamp when the virtual user was created
	 */
	created_at?: string;
};

