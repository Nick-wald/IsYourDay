

export type Body_upload_files_file_upload_post = {
	files: Array<Blob>;
	/**
	 * 是否公开文件
	 */
	is_public?: boolean;
	/**
	 * 是否使用流式处理（推荐大文件使用）
	 */
	use_streaming?: boolean;
};

