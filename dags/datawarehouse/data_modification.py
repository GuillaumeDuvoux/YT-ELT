import logging

logger = logging.getLogger(__name__)
table = "yt_api"


def insert_rows(cur, conn, schema, row):

    try:
        # normalize the row values to ensure required keys exist and to avoid
        # KeyError during parameter interpolation. We also provide sensible
        # defaults for count fields.
        if schema == "staging":
            video_id_key = "video_id"
            params = {
                "video_id": row.get("video_id"),
                "title": row.get("title"),
                "publishedAt": row.get("publishedAt"),
                "duration": row.get("duration"),
                "viewCount": row.get("viewCount", row.get("view_count")) ,
                "likeCount": row.get("likeCount"),
                "commentCount": row.get("commentCount"),
            }

            cur.execute(
                f"""
                INSERT INTO {schema}.{table}("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Views", "Likes_Count", "Comments_Count")
                VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s);
                """,
                params,
            )
        else:
            video_id_key = "Video_ID"
            params = {
                "Video_ID": row.get("Video_ID"),
                "Video_Title": row.get("Video_Title"),
                "Upload_Date": row.get("Upload_Date"),
                "Duration": row.get("Duration"),
                "Video_Type": row.get("Video_Type"),
                "Video_Views": row.get("Video_Views"),
                "Likes_Count": row.get("Likes_Count"),
                "Comments_Count": row.get("Comments_Count"),
            }
            cur.execute(
                f"""
                INSERT INTO {schema}.{table}("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Type", "Video_Views", "Likes_Count", "Comments_Count")
                VALUES (%(Video_ID)s, %(Video_Title)s, %(Upload_Date)s, %(Duration)s, %(Video_Type)s, %(Video_Views)s, %(Likes_Count)s, %(Comments_Count)s)
                """,
                params,
            )

        conn.commit()

        logger.info(f"Inserted row with Video_ID: {row.get(video_id_key)}")

    except Exception as e:
        vid = row.get(video_id_key, "<unknown>")
        logger.error(f"Error inserting row with Video_ID: {vid} - {e}")
        raise e


def update_rows(cur, conn, schema, row):

    try:
        # build a normalized parameter map similar to insert_rows
        if schema == "staging":
            params = {
                "video_id": row.get("video_id"),
                "publishedAt": row.get("publishedAt"),
                "title": row.get("title"),
                "viewCount": row.get("viewCount", row.get("view_count")),
                "likeCount": row.get("likeCount"),
                "commentCount": row.get("commentCount"),
            }
            video_id = "video_id"
            upload_date = "publishedAt"
            video_title = "title"
            video_views = "viewCount"
            likes_count = "likeCount"
            comments_count = "commentCount"
        else:
            params = row  # core already uses correct keys; counts default handled above if necessary
            video_id = "Video_ID"
            upload_date = "Upload_Date"
            video_title = "Video_Title"
            video_views = "Video_Views"
            likes_count = "Likes_Count"
            comments_count = "Comments_Count"

        cur.execute(
            f"""
            UPDATE {schema}.{table}
            SET "Video_Title" = %({video_title})s,
                "Video_Views" = %({video_views})s, 
                "Likes_Count" = %({likes_count})s, 
                "Comments_Count" = %({comments_count})s
            WHERE "Video_ID" = %({video_id})s AND "Upload_Date" = %({upload_date})s;
            """,
            params,
        )

        conn.commit()

        logger.info(f"Updated row with Video_ID: {params.get(video_id)}")

    except Exception as e:
        vid = params.get(video_id, "<unknown>")
        logger.error(f"Error updating row with Video_ID: {vid} - {e}")
        raise e


def delete_rows(cur, conn, schema, ids_to_delete):

    try:

        ids_to_delete = f"""({', '.join(f"'{id}'" for id in ids_to_delete)})"""

        cur.execute(
            f"""
            DELETE FROM {schema}.{table}
            WHERE "Video_ID" IN {ids_to_delete};
            """
        )

        conn.commit()
        logger.info(f"Deleted rows with Video_IDs: {ids_to_delete}")

    except Exception as e:
        logger.error(f"Error deleting rows with Video_IDs: {ids_to_delete} - {e}")
        raise e