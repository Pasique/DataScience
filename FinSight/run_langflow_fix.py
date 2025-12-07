import sys
import builtins
from typing import AsyncGenerator, Optional, List, Dict, Any, Union

import sys
import builtins
from typing import AsyncGenerator, Optional, List, Dict, Any, Union

# --- PATCH PARA PYTHON 3.13 ---
# Injeta tipos comuns no builtins para que o inspect.signature(eval_str=True) do FastAPI consiga resolvê-los
builtins.AsyncGenerator = AsyncGenerator
builtins.Optional = Optional
builtins.List = List
builtins.Dict = Dict
builtins.Any = Any
builtins.Union = Union

# Patch para AsyncSession
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    builtins.AsyncSession = AsyncSession
except ImportError:
    pass

# Patch massivo para Serviços do LangFlow
services_to_patch = [
    ("langflow.services.auth.service", "AuthService"),
    ("langflow.services.cache.service", "CacheService"),
    ("langflow.services.chat.service", "ChatService"),
    ("langflow.services.database.service", "DatabaseService"),
    ("langflow.services.job_queue.service", "JobQueueService"),
    ("langflow.services.session.service", "SessionService"),
    ("langflow.services.settings.service", "SettingsService"),
    ("langflow.services.socket.service", "SocketService"),
    ("langflow.services.storage.service", "StorageService"),
    ("langflow.services.task.service", "TaskService"),
    ("langflow.services.variable.service", "VariableService"),
    ("langflow.services.telemetry.service", "TelemetryService"),
    ("langflow.services.tracing.service", "TracingService"),
    ("langflow.services.store.service", "StoreService"),
    ("langflow.services.shared_component_cache.service", "SharedComponentCacheService"),
]

for module_path, class_name in services_to_patch:
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        setattr(builtins, class_name, cls)
    except (ImportError, AttributeError) as e:
        # Silencioso ou print para debug se necessário
        pass

# ------------------------------

from langflow.__main__ import main

if __name__ == "__main__":
    sys.argv = ["langflow", "run"]
    main()

from langflow.__main__ import main

if __name__ == "__main__":
    # Simula os argumentos da linha de comando "langflow run"
    sys.argv = ["langflow", "run"]
    main()
