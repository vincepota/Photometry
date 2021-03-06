'''
Determine optimum aperture and use Source Extractor to get photometry
'''
import sys
import os
from subprocess import call, Popen, PIPE
import glob
import numpy as np
import Sources
import Quadtree
import createSexConfig
import createSexParam
import findBestAperture
import makeRegionFile
import phot_utils
import geom_utils

def get_photometry(system, in_images):
    galsub = []
    imgs = []
    with(open(in_images, "r")) as f:
        for line in f:
            cols = line.split()
            galsub.append(cols[0])
            imgs.append(cols[1])

    filter_file = "default.conv"
    param_file = createSexParam.createSexParam(system, False)

    for i, img in enumerate(imgs):
        image = phot_utils.load_fits(img, verbose=False)
        satur = image[0].header['SATURATE']
        seeing = 1
        #ap = ','.join(map(str, np.linspace(5.0, 10, 1)))
        #ap = findBestAperture.findBestAperture(img, satur, seeing)
        ap = 5.0
        fname = system + '_' + img[-12]
        # Extract sources with initial rough estimate of seeing
        config = createSexConfig.createSexConfig(fname, filter_file,
                 param_file, satur, seeing, "nill", ap, False)
        call(['sex', '-c', config, galsub[i], img])
        seeing = phot_utils.calc_seeing(fname + '.cat')

        # Re_extract with refined seeing
        config = createSexConfig.createSexConfig(fname, filter_file,
                 param_file, satur, seeing, "nill", ap, False)
        call(['sex', '-c', config, galsub[i], img])

        ## Re-name the check images created
        ## This doesn't work as intended
        #checks = (glob.glob('*.fits'))
        #for check in checks:
        #    os.rename(check, fname + '_' + check)

def main():
    get_photometry(sys.argv[1], sys.argv[2])

    with open('NGC4621_i.cat', 'r') as catalog:
        tmp = filter(lambda line: phot_utils.no_head(line), catalog)
        tmp2 = map(lambda line: Sources.SCAMSource(line), tmp)
    ra = map(lambda line: line.ra, tmp2)
    dec = map(lambda line: line.dec, tmp2)

    i_sources = Quadtree.ScamEquatorialQuadtree(min(ra), min(dec),
                                              max(ra), max(dec))
    with open('NGC4621_i.cat', 'r') as catalog:
        tmp = filter(lambda line: phot_utils.no_head(line), catalog)
        map(lambda line: i_sources.insert(Sources.SCAMSource(line)), tmp)
        makeRegionFile.makeRegionFile('NGC4621_i.cat', 'NGC4621_i.reg', 10, 'blue')

    with open('NGC4621_g.cat', 'r') as catalog:
        tmp = filter(lambda line: phot_utils.no_head(line), catalog)
        tmp2 = map(lambda line: Sources.SCAMSource(line), tmp)
    ra = map(lambda line: line.ra, tmp2)
    dec = map(lambda line: line.dec, tmp2)

    g_sources = Quadtree.ScamEquatorialQuadtree(min(ra), min(dec),
                                              max(ra), max(dec))
    with open('NGC4621_g.cat', 'r') as catalog:
        tmp = filter(lambda line: phot_utils.no_head(line), catalog)
        map(lambda line: g_sources.insert(Sources.SCAMSource(line)), tmp)
        makeRegionFile.makeRegionFile('NGC4621_g.cat', 'NGC4621_g.reg', 10, 'blue')

    # Aaron gave me the coordinates
    m59_ucd3_i = i_sources.match(190.54601, 11.64478)
    m59_ucd3_g = g_sources.match(190.54601, 11.64478)

    print '\n'

    print "M58-UCD3's Location in catalog: ", m59_ucd3_i.name
    print "I Mag and G Mag: ",  m59_ucd3_i.mag_auto, m59_ucd3_g.mag_auto
    print 'M59-UCD3 g-i: ', m59_ucd3_g.mag_auto - m59_ucd3_i.mag_auto
    print 'M59-UCD3 FWHM: ', m59_ucd3_g.fwhm*0.2
    print "Coordinates from i-band catalog - "
    print phot_utils.convertRA(m59_ucd3_i.ra), phot_utils.convertDEC(m59_ucd3_i.dec)
    print "Coordinates from g-band catalog - "
    print phot_utils.convertRA(m59_ucd3_g.ra), phot_utils.convertDEC(m59_ucd3_g.dec)

    print '\n'
    print '\n'

    m59cO_i = i_sources.match(190.48056, 11.66771)
    m59cO_g = g_sources.match(190.48056, 11.66771)
    print "M59cO's Location in catalog: ", m59cO_i.name
    print "I Mag and G Mag: ", m59cO_i.mag_auto, m59cO_g.mag_auto
    print 'M59cO g-i: ', m59cO_g.mag_auto - m59cO_i.mag_auto
    print "Coordinates from i-band catalog - "
    print phot_utils.convertRA(m59cO_i.ra), phot_utils.convertDEC(m59cO_i.dec)
    print "Coordinates from g-band catalog - "
    print phot_utils.convertRA(m59cO_g.ra), phot_utils.convertDEC(m59cO_g.dec)

    print '\n'

    #M59_GCX = sources.match(190.50245, 11.65993)
    #print M59_GCX.name
    #print phot_utils.convertRA(M59_GCX.ra), phot_utils.convertDEC(M59_GCX.dec)

    #M59_GCY = sources.match(190.51231, 11.63986)
    #print M59_GCY.name
    #print phot_utils.convertRA(M59_GCY.ra), phot_utils.convertDEC(M59_GCY.dec)

    #NGC_4621_AIMSS1 = sources.match(190.47050, 11.63001)
    #print NGC_4621_AIMSS1.name
    #print phot_utils.convertRA(NGC_4621_AIMSS1.ra), phot_utils.convertDEC(NGC_4621_AIMSS1.dec)

if __name__ == '__main__':
    sys.exit(main())

