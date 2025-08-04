

/**
 * Data model for creating a new virtual user. 
 */
export type VirtualUserPublic = {
	real_name?: string | null;
	sex?: number;
	birthday?: string | null;
	tel?: string | null;
	prompt?: string | null;
	location?: string | null;
	QQ?: string | null;
	wechat?: string | null;
	identify?: string | null;
	email: string;
};

