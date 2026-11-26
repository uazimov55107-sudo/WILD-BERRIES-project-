package com.wildberries.control

import android.content.Context
import android.content.pm.ApplicationInfo

data class SecurityReport(val checks: Map<String, Boolean>) {
    val isSecure: Boolean
        get() = checks.values.all { it }
}

object SecurityAgent {
    fun inspect(context: Context): SecurityReport {
        val info = context.applicationContext.applicationInfo

        return SecurityReport(
            mapOf(
                "not_debuggable" to
                    (info.flags and ApplicationInfo.FLAG_DEBUGGABLE == 0),
                "backup_disabled" to
                    (info.flags and ApplicationInfo.FLAG_ALLOW_BACKUP == 0)
            )
        )
    }
}
