

/**
 * File model for storing file metadata.
 */
export type FileDB = {
	/**
	 * Unique identifier for the file
	 */
	id?: string;
	/**
	 * Name of the file
	 */
	name: string;
	/**
	 * MD5 hash of the file for integrity check
	 */
	md5: string;
	/**
	 * Is the file publicly accessible?
	 */
	is_public?: boolean;
	/**
	 * Path to the file on the server
	 */
	path: string;
	/**
	 * Size of the file in bytes
	 */
	size?: number;
	/**
	 * ID of the user who uploaded the file
	 */
	uploader_id: string | null;
	/**
	 * Timestamp when the file was uploaded
	 */
	upload_time?: string;
};

