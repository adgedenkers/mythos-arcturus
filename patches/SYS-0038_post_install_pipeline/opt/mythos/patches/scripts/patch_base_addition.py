# This is the code to insert at the end of PatchBase.finish(), right before the final self.logger.write_logs(result) call

        # ── Post-install pipeline ──────────────────────────────────────────
        if not self.dry_run and len(self.errors) == 0:
            try:
                from post_install import run_pipeline
                pipeline_results = run_pipeline(
                    patch_id=self.patch_id,
                    stream=self.stream,
                    number=self.number,
                    description=self.description,
                    patch_type=self.patch_type,
                    files_deployed=self.files_deployed,
                    services_restarted=self.services_restarted,
                    sql_run=self.sql_run,
                    errors=self.errors,
                )
                result['pipeline'] = pipeline_results
            except Exception as e:
                self.logger.log(f"  ⚠ Post-install pipeline failed: {e}")
                result['pipeline_error'] = str(e)
