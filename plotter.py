import os
import argparse
import random
import string
import yaml
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import uproot as ur
from pathlib import Path


def parse_plot_cfg(cfg_file):
    with open(cfg_file, 'r') as f:
        raw_config = yaml.safe_load(f)

    return raw_config


def get_data(cfg, cache):
    for entry in cache:
        if entry['inputs'] == cfg['inputs'] and \
           entry['cuts'] == cfg['cuts'] and \
           entry['branches'] == cfg['branches']:

            return entry['data']

    tree = cfg.get('tree', 'Events')
    inputs = []
    for f in cfg['inputs']:
        if Path(f).is_file():
            inputs.append(f'{f}:{tree}')
        elif Path(f).is_dir():
            inputs.append(f'{f.rstrip("/")+"/*.root"}:{tree}')
        else:
            print(f'file/dir {f} not fount')

    cuts = cfg['cuts'].strip('\n') if cfg['cuts'] is not None else None
    raw_data = ur.concatenate(
        inputs,
        expressions=cfg['branches'],
        cut=cuts,
        library='ak',
    )

    data = {
        key: raw_data[key].to_numpy() if raw_data[key].ndim == 1
        else raw_data[key][:, 0].to_numpy()
        for key in cfg['branches']
    }
    cache.append({
        'inputs': cfg['inputs'],
        'cuts': cfg['cuts'],
        'branches': cfg['branches'],
        'data': data,
    })

    return data


def make_plot(data, ax, cfg):
    for i, branch in enumerate(cfg['branches']):
        if cfg.get('norm', False):
            weights = np.ones_like(data[branch]) / len(data[branch])
        else:
            weights = np.ones_like(data[branch])
        hist, bin_edges = np.histogram(data[branch], bins=np.linspace(*cfg['bins']), weights=weights)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        ax.errorbar(
            bin_centers,
            hist,
            yerr=0,
            marker='',
            drawstyle='steps-mid',
            label=None if cfg['legend'] is None else cfg['legend'][i],
        )


def configure_ax(fig, ax, cfg):
    xlabel = cfg.get('xlabel', 'X Axis')
    ax.set_xlabel(xlabel, loc='right')

    ylabel = cfg.get('ylabel', 'nEntries [A.U.]')
    ax.set_ylabel(ylabel, loc='top')

    yscale = cfg.get('scale', 'linear')
    ax.set_yscale(yscale)

    if cfg['legend'] is not None:
        ax.legend()


def save_plot(fig, cfg):
    output_dir = Path(cfg.get('output_dir', '.'))
    os.makedirs(output_dir, exist_ok=True)

    filename = cfg.get('filename', 'plot_'+''.join(random.choices(string.ascii_lowercase + string.digits, k=6)))

    output_path = output_dir / Path(filename+'.png')
    fig.savefig(output_path)
    fig.savefig(output_path.with_suffix('.pdf'))


def plot_inputs(args):
    # plt.style.use(hep.style.CMS)
    plots_cfg = parse_plot_cfg(args.config)
    cached_data = []
    for plot, plot_cfg in plots_cfg['plots'].items():
        if plot_cfg.get('skip', False):
            continue
        print(f"{'Plotting '+plot+' ':.<60} \u2610", end="", flush=True)
        data = get_data(plot_cfg, cached_data)
        fig, ax = plt.subplots(figsize=(8, 6))
        hep.cms.label(loc=0, ax=ax, data=bool(plot_cfg.get('data',False)), year=2022,com=13.6)
        make_plot(data, ax, plot_cfg)
        configure_ax(fig, ax, plot_cfg)
        save_plot(fig, plot_cfg)
        plt.close()
        print(f"\r{'Plotting '+plot+' ':.<60} \u2611")


def main(args):
    plot_inputs(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=Path, required=True, help='Plot configuration file')
    args = parser.parse_args()

    main(args)