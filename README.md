# Automatic Log Tracker for Deep Learning Experiments

|worker-name| acc | lr |
|---|---|---|
|w0 | 0.9| 0.001|
|   | 0.8| 0.0005|

# how to use

## step 1
share spreadsheet to email: clerkx@log-clerk.iam.gserviceaccount.com

install clerk:
```
pip install git+https://github.com/LiyuanLucasLiu/clerk.git
```

get clerk credential and store it to the config path: CLERK_CONFIG

## usage case 1:

```
clerk config -ss spread-sheet-name -ws work-sheet-name -w worker-name

preset=$(clerk new-run)

while [ $preset == 'preset_found' ]
do
    bash sub_run.sh $OUTPUT_DIR $LOAD_DIR "$(clerk get-args learning_rate batch_size epochs warmup)"
    preset=$(clerk new-run)
done
```

## usage case 2:

```
from clerk import init_clerk_logger
init_clerk_logger(rank=distributed_utils.get_global_rank())

class ClerkSimpleProgressBar(BaseProgressBar):
    """A minimal logger for non-TTY environments."""

    def __init__(self, iterable, epoch=None, prefix=None, log_interval=1000):
        super().__init__(iterable, epoch, prefix)
        self.log_interval = log_interval
        self.i = None
        self.size = None

    def __iter__(self):
        self.size = len(self.iterable)
        for i, obj in enumerate(self.iterable, start=self.n):
            self.i = i
            yield obj
    
    def _str_commas(self, stats):
        return "; ".join(key + "=" + stats[key].strip() for key in stats.keys())
    
    def log(self, stats, tag=None, step=None):
        """Log intermediate stats according to log_interval."""
        step = step or self.i or 0
        if step > 0 and self.log_interval is not None and step % self.log_interval == 0:
            stats = self._format_stats(stats)
            postfix = self._str_commas(stats)
            with rename_logger(logger, tag):
                logger.info(
                    "[clerk] epoch={}; update_in_epoch={}; {}; {}".format(
                        self.epoch, self.i + 1, self.size, postfix
                    )
                )

    def print(self, stats, tag=None, step=None):
        """Print end-of-epoch stats."""
        postfix = self._str_pipes(self._format_stats(stats))
        with rename_logger(logger, tag):
            logger.info("{} | {}".format(self.prefix, postfix))
```

